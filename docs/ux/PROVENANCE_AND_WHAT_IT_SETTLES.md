# Provenance of the UX documents in this directory, and what they settle

**Brought into version control 2026-10-29T17:59:52+00:00.** Until that moment none of them was in the
repository and **nothing in the repository referenced them**, which is why this note exists
alongside them rather than inside them.

## Where they came from, and why that matters

The founder wrote them and placed them in `/Users/georgejackson/Developer_Projects/Responses/`
as 2 archives and 1 extracted directory:

| Source | Date on the file | Brought in as |
|---|---|---|
| `CDSFL_UX_Design_Brief_AUTHORITATIVE.zip` → `cdsfl_ux_v6/docs/CDSFL_UX_Design_Brief_AUTHORITATIVE_for_Orchestrator.md` | 2026-10-21 23:23 | `CDSFL_UX_Design_Brief_AUTHORITATIVE_for_Orchestrator.md` |
| same archive | 2026-10-21 16:17 | `Explorer_Meta_Tooltip_for_Orchestrator.md` |
| same archive | 2026-10-21 01:41 | `Explorer_Read_More_Technical_Note_Outline.md` |
| same archive | 2026-10-21 22:32 | `README_HELP_PATTERN.md` |
| same archive | 2026-10-21 23:23 | `PACKAGE_README.md` |
| `cdsfl_ux_BESTOF_2026-10-23/README.md` | 2026-10-24 01:10 | `BESTOF_SCREENS_README.md` |

**Every one is byte-identical to his original**, verified with `cmp` at copy time. Nothing was
reworded, reordered or annotated: this note is a separate file precisely so that his document
stays his. The screenshot pack itself (`screens/`, `html_sources/`) is left where he put it,
because it is image data rather than specification and his own pack README says
*"Screens are **illustrative**"* and that the brief is authoritative over the pixels.

## How they were found, which is the part worth recording

They were found on 2026-10-29 while answering `fr:36150569bed0`, an annotation of his on the
2026-10-19 morning report. His words there include *"perhaps what you lack is a clear
specification for what the orchestrator should do?"* and *"I have included some basic mock-ups
of how ultimately I envisage the CDSFL UX to look and to ultimately work."*

**He had already supplied the specification and it had not been read.** A search of the tree
for `AUTHORITATIVE` returned nothing; a search for anything referencing the brief returned 2
files, neither of which names it (the response-file reader matches the word for
unrelated reasons, and so does an August runway note). This is the failure shape recorded as *his words may not sit unread* and
*a seat's finding can sit in a sandbox*: a resource of his existed, outside the repository,
for 8 days, while an entry in the master task list recorded its subject as unspecified.

## What they settle, and what they do not

**They settle the premise of entry B20.** That entry reads *"his design is specified, nothing is
built"* and is DEFERRED on his own ruling placing it after the rest of the list. The brief is
that specification, and it goes considerably further than the entry assumes: section 15 gives an
implementation ORDER of 9 steps and section 16 gives 12 ACCEPTANCE CHECKS. So the deferral
stands on his instruction, but the entry's description of what exists is superseded.

**They answer the bounded-orchestrator question directly.** His question was whether the
orchestrator could be built bound, or whether CC1 was arguing against binding. Section 2 rule 2
answers it as a product rule: *"The **Orchestrator** seat is bound by the same experimental
rules as other seats. Binding is behaviour; the tab is simply named **Orchestrator**."* Section
5 adds that the title is *"**Orchestrator** (not "Bounded orchestrator")"*. So binding is not in
question; naming it in the interface is settled against the longer label.

**They answer half of entry B22.** B22 asks *"whether this is yet a general-purpose STEM
calculator"*. Section 1 declares the product identity: *"CDSFL is a **local-first
general-purpose STEM calculator and experiment instrument**, not a multi-tenant chat website and
not a configuration console for its own internals."* That is a statement of intent rather than a
measurement of present capability, so it fixes the TARGET without settling whether the harness
has reached it — which is the half the panel question still asks.

**They do NOT settle what a fix means outside code**, which is B22's other half and the subject
of the panel brief at `bench/logs/stem_generality_b22_2026-10-29/BRIEF.md`. Section 2 rule 1
bears on it — *"Claims are **not** cleared by chat, Discourse, or comments. Only mechanical
checks and explicit human residual acceptance settle outcomes"* — and that is informative rather
than decisive: it names human residual acceptance as a settling route, which is a candidate home
for *"correctly identified, not repairable by edit"*, and it does not say so in those terms.

**They do not authorise any build.** The implementation order is his design, not an instruction
to start; entry B20 remains deferred where he placed it.

## What is owed, derived from his annotation rather than invented

His 2026-10-19 words ask for 2 specifications that this package does not contain:

1. **A specification of the orchestrator's function derived from CC1's present role** — *"Primarily the orchestrator should perform all of the functions you currently perform. ... perhaps you should consider deeply what your current role is and then define it as a specification?"*
2. **An interaction specification for the human in the loop** — *"as well as drawing up a specification for the HIL, you should draw up an interaction specification or me, and use this in your experiments that involve the new orchestrator?"* (*"or me"* is *"for me"*.)

Both are owed by CC1 and neither exists. They are the live residue of `fr:36150569bed0`.

Written under CDSFL note standard v1.8 (17 October 2026).
